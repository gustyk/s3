import simpy
import yaml
from src.order_generator import generate_orders

# Helper class to simulate order pool
class OrderPool:
    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

# Main testing function
def test_order_generator():
    # Load parameters from config/parameters.yaml
    with open("config/parameters.yaml", "r") as file:
        params = yaml.safe_load(file)

    # Extract selected configuration
    selected_config = params["SELECTED_CONFIGURATION"]
    arrival_rate_key = selected_config["incoming_rate"]
    arrival_rate = params["incoming_rate"][(arrival_rate_key)]
    simulation_time = params["simulation_time"]

    # Initialize SimPy environment and order pool
    env = simpy.Environment()
    order_pool = OrderPool()

    # Run the order generator process
    env.process(generate_orders(env, order_pool, arrival_rate, simulation_time))
    env.run()

    # Analyze results
    orders = order_pool.orders
    interarrival_times = [
        (orders[i]["Created Time"], orders[i - 1]["Created Time"])
        for i in range(1, len(orders))
    ]
    interarrival_times_seconds = [
        int(created_time.split(":")[0]) * 3600
        + int(created_time.split(":")[1]) * 60
        + int(created_time.split(":")[2])
        - (
            int(previous_time.split(":")[0]) * 3600
            + int(previous_time.split(":")[1]) * 60
            + int(previous_time.split(":")[2])
        )
        for created_time, previous_time in interarrival_times
    ]

    # Print summary
    print(f"Total Orders Generated: {len(orders)}")
    print(f"Expected Orders (λ={arrival_rate} orders/min): {arrival_rate * (simulation_time / 60):.2f}")
    print(f"Average Interarrival Time: {sum(interarrival_times_seconds) / len(interarrival_times_seconds):.2f} seconds")
    print("\nFirst 5 Orders:")
    for order in orders[:5]:
        print(order)

# Run the test
if __name__ == "__main__":
    test_order_generator()