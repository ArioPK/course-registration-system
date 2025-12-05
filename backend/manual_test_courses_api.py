# backend/manual_test_courses_api.py

import requests

BASE_URL = "http://127.0.0.1:8000"

def get_token(username: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
    )
    print("Login status:", resp.status_code)
    print("Login response:", resp.json())
    resp.raise_for_status()
    return resp.json()["access_token"]


def main() -> None:
    token = get_token("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a course
    course_payload = {
        "code": "CS-API-101",
        "name": "API Test Course",
        "capacity": 30,
        "professor_name": "Dr. API",
        "day_of_week": "SAT",
        "start_time": "10:00:00",
        "end_time": "11:30:00",
        "location": "API Room",
    }

    print("\n=== Creating course via API ===")
    resp = requests.post(f"{BASE_URL}/courses/", json=course_payload, headers=headers)
    print("Create status:", resp.status_code)
    print("Create response:", resp.json())
    resp.raise_for_status()
    course = resp.json()
    course_id = course["id"]

    print("\n=== Listing courses via API ===")
    resp = requests.get(f"{BASE_URL}/courses/", headers=headers)
    print("List status:", resp.status_code)
    print("List response:", resp.json())
    resp.raise_for_status()

    print("\n=== Deleting course via API ===")
    resp = requests.delete(f"{BASE_URL}/courses/{course_id}", headers=headers)
    print("Delete status:", resp.status_code)
    if resp.status_code != 204:
        print("Delete response:", resp.json())

    print("\nManual Course CRUD API test finished.")

if __name__ == "__main__":
    main()
