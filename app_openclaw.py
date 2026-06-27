from agents.booking_agent import BookingAgent
import json
import sys 

def main():
    print("⚡ EV Booking Assistant")
    print("Type 'exit' to quit.\n")

    agent = BookingAgent()   
    # Command-line mode (used by OpenClaw)
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = agent.run(request)
        print(json.dumps(result["final_outcome"], indent=2))
        return

    while True:
        request = input("User: ")

        if request.lower() in ["exit", "quit"]:
            break

        try:
            result = agent.run(request)

            print("\nResult:\n")
            print(json.dumps(result["final_outcome"], indent=2))

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
