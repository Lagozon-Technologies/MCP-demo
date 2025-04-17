import requests

def test_multiply(a, b):
    response = requests.post("http://127.0.0.1:8000/euron/mcp/multiply", json={"a": a, "b": b})
    if response.status_code == 200:
        print("Multiplication MCP called successfully:", response.json()["result"])
    else:
        print("There was an issue with multiply.")

def test_get_alerts(state_code):
    response = requests.post("http://127.0.0.1:8000/euron/mcp/get_alerts", json={"state": state_code})
    if response.status_code == 200:
        print(f"Weather alerts for {state_code}:\n{response.json()['alerts']}")
    else:
        print("There was an issue with get_alerts.")

if __name__ == "__main__":
    test_multiply(2, 3)
    test_get_alerts("CA")  # You can try "NY", "TX", etc.
