import math
import rclpy
from auto_drive import AutoDrive


class KNNPriorityModel:
    """Example-based machine learning model for patrol priority."""

    def __init__(self, k=5):
        self.k = k
        self.samples = []

        # Synthetic training examples:
        # urgency (1-5), distance (m), priority score.
        for urgency in range(1, 6):
            for distance in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5):
                score = 2.0 * urgency - 2.0 * distance
                if urgency == 5:
                    score += 1.5
                self.samples.append((urgency, distance, score))

    def predict(self, urgency, distance):
        neighbors = []

        for u, d, score in self.samples:
            # Normalize feature scales for neighbor search.
            metric = math.sqrt(
                ((urgency - u) / 5.0) ** 2
                + ((distance - d) / 1.5) ** 2
            )
            neighbors.append((metric, score))

        neighbors.sort(key=lambda item: item[0])
        selected = neighbors[:self.k]

        weights = [1.0 / (dist + 0.001) for dist, _ in selected]

        return sum(
            w * item[1] for w, item in zip(weights, selected)
        ) / sum(weights)


class AIPatrol(AutoDrive):
    def __init__(self):
        super().__init__()
        self.model = KNNPriorityModel(k=5)

        # Coordinates relative to starting position.
        locations = [
            ("A: Normal inspection", 0.8, 0.0, 5),
            ("B: Equipment alert", 0.8, 0.8, 2),
            ("C: Periodic inspection", 0.0, 0.8, 3),
        ]

        ranked = []

        for name, x, y, urgency in locations:
            distance = math.hypot(x, y)
            score = self.model.predict(urgency, distance)
            ranked.append((score, name, x, y))

        ranked.sort(reverse=True)

        self.waypoints = [
            (x, y) for score, name, x, y in ranked
        ]
        self.waypoints.append((0.0, 0.0))

        self.get_logger().info("=== AI PATROL PLANNING ===")
        self.get_logger().info(
            f"KNN training examples: {len(self.model.samples)}"
        )

        for index, (score, name, x, y) in enumerate(ranked, 1):
            self.get_logger().info(
                f"{index}. {name}: predicted score={score:.2f}"
            )

        self.get_logger().info(
            "AI inference complete. Starting patrol."
        )


def main():
    rclpy.init()
    node = AIPatrol()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(
            __import__('geometry_msgs.msg',
                       fromlist=['Twist']).Twist()
        )
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
