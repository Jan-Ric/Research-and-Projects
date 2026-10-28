import cv2
import os
import numpy as np
from pathlib import Path
import argparse
from typing import Tuple, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoFrameExtractor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Supported video formats
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}

    def calculate_frame_quality(self, frame: np.ndarray) -> float:
        """
        Calculate frame quality based on multiple metrics:
        - Sharpness (Laplacian variance)
        - Contrast (standard deviation)
        - Brightness balance
        - Edge density
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()

        # 2. Contrast (standard deviation of pixel intensities)
        contrast = gray.std()

        # 3. Brightness balance (distance from ideal brightness)
        mean_brightness = gray.mean()
        brightness_score = 1.0 - abs(mean_brightness - 127.5) / 127.5

        # 4. Edge density using Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Combine metrics with weights
        quality_score = (
                sharpness * 0.4 +  # Sharpness is most important
                contrast * 0.3 +  # Contrast for visual appeal
                brightness_score * 100 * 0.2 +  # Brightness balance
                edge_density * 1000 * 0.1  # Edge density for detail
        )

        return quality_score

    def calculate_lighting_quality(self, frame: np.ndarray) -> float:
        """
        Calculate lighting quality based on:
        - Histogram distribution
        - Dynamic range
        - Exposure balance
        """
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 1. Histogram distribution (avoid too many pixels in extreme values)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        total_pixels = frame.shape[0] * frame.shape[1]

        # Penalize overexposure (too many bright pixels)
        overexposed = np.sum(hist[240:]) / total_pixels
        # Penalize underexposure (too many dark pixels)
        underexposed = np.sum(hist[:16]) / total_pixels
        exposure_penalty = (overexposed + underexposed) * 100

        # 2. Dynamic range (difference between max and min non-zero values)
        non_zero_pixels = gray[gray > 0]
        if len(non_zero_pixels) > 0:
            dynamic_range = np.max(non_zero_pixels) - np.min(non_zero_pixels)
        else:
            dynamic_range = 0

        # 3. Value channel distribution in HSV
        v_channel = hsv[:, :, 2]
        v_std = v_channel.std()

        # Combine lighting metrics
        lighting_score = (
                dynamic_range * 0.4 +  # Good dynamic range
                v_std * 0.3 +  # Good value distribution
                (100 - exposure_penalty) * 0.3  # Penalize poor exposure
        )

        return max(0, lighting_score)

    def find_best_frame(self, video_path: str) -> Tuple[np.ndarray, int, float]:
        """
        Find the best frame from a video based on quality and lighting.
        Returns the best frame, frame number, and combined score.
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        logger.info(f"Processing {total_frames} frames from {Path(video_path).name}")

        best_frame = None
        best_score = -1
        best_frame_num = -1

        # Sample frames (every 30th frame for efficiency, adjust as needed)
        frame_interval = max(1, total_frames // 100)  # Sample ~100 frames max

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames based on interval
            if frame_count % frame_interval == 0:
                try:
                    # Calculate quality and lighting scores
                    quality_score = self.calculate_frame_quality(frame)
                    lighting_score = self.calculate_lighting_quality(frame)

                    # Combined score (adjust weights as needed)
                    combined_score = quality_score * 0.7 + lighting_score * 0.3

                    if combined_score > best_score:
                        best_score = combined_score
                        best_frame = frame.copy()
                        best_frame_num = frame_count

                        # Log progress for very good frames
                        if combined_score > best_score * 0.9:
                            timestamp = frame_count / fps if fps > 0 else 0
                            logger.info(
                                f"New best frame at {timestamp:.2f}s (frame {frame_count}), score: {combined_score:.2f}")

                except Exception as e:
                    logger.warning(f"Error processing frame {frame_count}: {e}")

            frame_count += 1

        cap.release()

        if best_frame is None:
            raise ValueError("No valid frames found in video")

        return best_frame, best_frame_num, best_score

    def process_video(self, video_path: str) -> bool:
        """Process a single video and extract the best frame."""
        try:
            logger.info(f"Processing video: {video_path}")

            # Find best frame
            best_frame, frame_num, score = self.find_best_frame(video_path)

            # Generate output filename
            video_name = Path(video_path).stem
            output_filename = f"{video_name}_best_frame_{frame_num}.jpg"
            output_path = self.output_dir / output_filename

            # Save the best frame
            cv2.imwrite(str(output_path), best_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

            logger.info(f"Extracted best frame (score: {score:.2f}) to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")
            return False

    def process_directory(self) -> None:
        """Process all videos in the input directory."""
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        # Find all video files
        video_files = []
        for ext in self.video_extensions:
            video_files.extend(self.input_dir.glob(f"*{ext}"))
            video_files.extend(self.input_dir.glob(f"*{ext.upper()}"))

        if not video_files:
            logger.warning(f"No video files found in {self.input_dir}")
            return

        logger.info(f"Found {len(video_files)} video files to process")

        # Process each video
        successful = 0
        for video_file in video_files:
            if self.process_video(str(video_file)):
                successful += 1

        logger.info(f"Successfully processed {successful}/{len(video_files)} videos")


def main():
    parser = argparse.ArgumentParser(description="Extract best quality frames from videos")
    parser.add_argument("input_dir", help="Directory containing video files")
    parser.add_argument("output_dir", help="Directory to save extracted frames")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        extractor = VideoFrameExtractor(args.input_dir, args.output_dir)
        extractor.process_directory()

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Example usage when run directly
    import sys

    if len(sys.argv) < 3:
        print("Usage: python video_frame_extractor.py <input_directory> <output_directory>")
        print("Example: python video_frame_extractor.py ./videos ./extracted_frames")
        sys.exit(1)

    sys.exit(main())