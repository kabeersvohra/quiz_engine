from app import app
import json
from fastapi.testclient import TestClient

client = TestClient(app)

john_credentials = {
    "email": "john@gmail.com",
    "password": "johnny"
}

jim_credentials = {
    "email": "jim@gmail.com",
    "password": "jimmy"
}

quiz_1 = {
    "name": "Quiz 1",
    "questions": [
        {
            "question": "Moon is a star",
            "type": "single",
            "answers": [
                {
                    "answer": "yes",
                    "correct": False
                },
                {
                    "answer": "no",
                    "correct": True
                }
            ]
        },
        {
            "question": "Temperature can be measured in",
            "type": "multi",
            "answers": [
                {
                    "answer": "kelvin",
                    "correct": True
                },
                {
                    "answer": "farenheit",
                    "correct": True
                },
                {
                    "answer": "gram",
                    "correct": False
                },
                {
                    "answer": "celsius",
                    "correct": True
                },
                {
                    "answer": "litres",
                    "correct": False
                }
            ]
        }
    ]
}

quiz_2 = {
    "name": "Quiz 2",
    "questions": [
        {
            "question": "Bill Gates is rich",
            "type" : "single",
            "answers": [
                {
                    "answer": "yes",
                    "correct": True
                },
                {
                    "answer": "no",
                    "correct": False
                }
            ]
        }
    ]
}

quiz_2_no_answers = {
    "name": "Quiz 2",
    "questions": [
        {
            "question": "Bill Gates is rich",
            "type" : "single",
            "answers": [
                {
                    "answer": "yes",
                },
                {
                    "answer": "no",
                }
            ]
        }
    ]
}


def test_status():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"status": "OK"} 


def test_unauthenticated():
    headers = {"Authorization": "Bearer fake_token"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 403
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_user():
    data = {
        "email": "test@example.com",
        "password": "password"
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['email'] == "test@example.com"


def test_cant_create_same_user_twice():
    data = {
        "email": "test@example.com",
        "password": "password"
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 200

    data = {
        "email": "test@example.com",
        "password": "password"
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 400


def test_create_user_and_login():
    data = {
        "email": "test@example.com",
        "password": "password"
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 200

    response = client.post("/login", json=data)
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_authentication():
    data = {
        "email": "test@example.com",
        "password": "password"
    }
    client.post("/signup", json=data)
    response = client.post("/login", json=data)
    assert response.status_code == 200
    jwt = response.json()['access_token']
    headers = {"Authorization": f"Bearer {jwt}"}

    response = client.get("/me", headers=headers)
    assert response.status_code == 200


def test_create_quiz_and_view():
    # signup as john
    client.post("/signup", json=john_credentials)
    # login
    response = client.post("/login", json=john_credentials)

    john_jwt_token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {john_jwt_token}"}

    response = client.post("/create/quiz", headers=headers, json=quiz_2)
    assert response.status_code == 200
    id = response.json()['id']

    response = client.get("/view/quiz", headers=headers, json={"id": id})
    assert response.status_code == 200

    quiz_2_response = response.json()
    for question in quiz_2_response["questions"]:
        del question["id"]
    assert quiz_2_response == quiz_2_no_answers


def test_full():
    # create accounts for john and jim
    client.post("/signup", json=john_credentials)
    client.post("/signup", json=jim_credentials)

    # get jwt tokens and create headers for both
    response = client.post("/login", json=john_credentials)
    john_jwt_token = response.json()['access_token']
    john_headers = {"Authorization": f"Bearer {john_jwt_token}"}

    response = client.post("/login", json=jim_credentials)
    jim_jwt_token = response.json()['access_token']
    jim_headers = {"Authorization": f"Bearer {jim_jwt_token}"}

    # john creates quiz 1 and jim creates quiz 2
    response = client.post("/create/quiz", headers=john_headers, json=quiz_1)
    quiz_1_id = response.json()['id']
    response = client.post("/create/quiz", headers=jim_headers, json=quiz_2)
    quiz_2_id = response.json()['id']

    # john edits his quiz 1
    old_quiz_1_id = quiz_1_id
    edit_quiz_1 = {"id": old_quiz_1_id, "new_quiz": quiz_1}
    response = client.post("/edit/quiz", headers=john_headers, json=edit_quiz_1)
    quiz_1_id = response.json()['id']
    # check that the quiz has been edited (id has been updated)
    assert quiz_1_id != old_quiz_1_id

    # check that the old quiz id has been deleted
    response = client.get("/view/quiz", headers=john_headers, json={"id": old_quiz_1_id})
    assert response.status_code == 404  # the id can no longer be found

    # jim attempts to view quiz 1 but cannot because it is not published
    response = client.get("/list/quiz/todo", headers=jim_headers)
    assert response.json() == []

    # john now publishes quiz 1
    response = client.put("/publish/quiz", headers=john_headers, json={"id": quiz_1_id})

    # jim can now see and solve quiz 1
    response = client.get("/list/quiz/todo", headers=jim_headers)
    assert len(response.json()) == 1
    quiz_id = response.json()[0]["id"]
    response = client.get("/view/quiz", headers=jim_headers, json={"id": quiz_id})
    quiz = response.json()
    questions = quiz["questions"]
    data = {
        "quiz_id": quiz_id,
        "answers": [
            {
                "question_id": questions[0]["id"],
                "indices": [1]
            },
            {
                "question_id": questions[1]["id"],
                "indices": [0, 1, 2]
            }
        ]
    }
    response = client.post("/create/solution", headers=jim_headers, json=data)
    assert response.status_code == 200

    # jim can now see his solution
    response = client.get("/list/solution/submitted", headers=jim_headers)
    solution = response.json()[0]

    # jim scored 100% for the first question and 16.6% for the second
    # jim gave two correct answers for the second and one wrong answer
    # scoring him 1/2 + 1/2 - 1/3 = 0.16666666666666663
    # in total jim got 58.3%
    assert solution["completed_by"] == "jim@gmail.com"
    assert solution["scores"] == [1.0, 0.16666666666666663]
    assert solution["total_score"] == 0.5833333333333333

    # john can also see the same solution for the quiz since he posted it
    response = client.get("list/solution/quiz", headers=john_headers)
    assert solution == response.json()[0]
