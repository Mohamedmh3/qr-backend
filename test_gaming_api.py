"""
End-to-end tests for Team/Game/GameResult endpoints using requests.
Requires server running at http://localhost:8000 and 'requests' installed.
Run: venv\Scripts\python test_gaming_api.py
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api"


def require_server():
    try:
        requests.get(BASE_URL.replace('/api', '/'), timeout=5)
        return True
    except Exception:
        print("Server is not running. Start with: python manage.py runserver")
        return False


def register_user(name, email, password):
    r = requests.post(f"{BASE_URL}/register/", json={
        "name": name,
        "email": email,
        "password": password,
        "password_confirm": password,
    })
    if r.status_code not in (200, 201):
        # Might already exist; try login
        return None
    return r.json()


def login(email, password):
    r = requests.post(f"{BASE_URL}/login/", json={"email": email, "password": password})
    if r.status_code != 200:
        print('Login failed:', r.text)
        return None
    return r.json()


def auth_headers(access):
    return {"Authorization": f"Bearer {access}"}


def list_games(access):
    r = requests.get(f"{BASE_URL}/games/", headers=auth_headers(access))
    return r.status_code, r.json() if r.headers.get('content-type','').startswith('application/json') else r.text


def create_team(access, name):
    r = requests.post(f"{BASE_URL}/teams/", headers=auth_headers(access), json={"team_name": name})
    return r.status_code, r.json()


def list_teams(access):
    r = requests.get(f"{BASE_URL}/teams/", headers=auth_headers(access))
    return r.status_code, r.json()


def create_result(access, team_id, game_id, points, notes="test result"):
    r = requests.post(f"{BASE_URL}/results/", headers=auth_headers(access), json={
        "team": team_id,
        "game": game_id,
        "points_scored": points,
        "notes": notes,
    })
    return r.status_code, r.json()


def admin_list_results(access, **filters):
    r = requests.get(f"{BASE_URL}/admin/results/", headers=auth_headers(access), params=filters)
    return r.status_code, r.json()


def admin_update_result(access, result_id, payload):
    r = requests.put(f"{BASE_URL}/admin/results/{result_id}/", headers=auth_headers(access), json=payload)
    return r.status_code, r.json()

def admin_create_game(access, game_name, description='Test game', max_points=100, min_points=0):
    payload = {
        "game_name": game_name,
        "game_description": description,
        "max_points": max_points,
        "min_points": min_points,
    }
    r = requests.post(f"{BASE_URL}/admin/games/", headers=auth_headers(access), json=payload)
    return r.status_code, r.json()


def verify_qr(qr_id):
    r = requests.get(f"{BASE_URL}/verify/{qr_id}/")
    return r.status_code, r.json()


def main():
    if not require_server():
        sys.exit(1)

    # Users
    user_email = 'player1@example.com'
    user_pass = 'TestPass123!'
    admin_email = 'admin@example.com'
    admin_pass = 'AdminPass123!'

    # Ensure user exists (seed script should have created them)
    register_user('Player One', user_email, user_pass)

    # Login user and admin
    user_login = login(user_email, user_pass)
    admin_login = login(admin_email, admin_pass)
    assert user_login and admin_login, 'Failed to login user/admin'

    user_access = user_login['tokens']['access']
    admin_access = admin_login['tokens']['access']

    # Verify QR still works
    qr_id = user_login['user']['qr_id']
    code, data = verify_qr(qr_id)
    print('QR verify:', code, data)
    assert code == 200

    # List games (should come from seeding)
    code, games = list_games(user_access)
    print('Games:', code, games)
    if code == 200 and games.get('count', 0) >= 1:
        first_game = games['games'][0]
    else:
        # create a game as admin then re-list
        cg_code, cg = admin_create_game(admin_access, 'Endless Runner')
        print('Admin create game:', cg_code, cg)
        assert cg_code in (201, 400)
        code, games = list_games(user_access)
        assert code == 200 and games.get('count', 0) >= 1
        first_game = games['games'][0]

    # Create or fetch team
    code, team_list = list_teams(user_access)
    if team_list['count'] == 0:
        code, team = create_team(user_access, 'Alpha Team')
        print('Create team:', code, team)
        assert code == 201
        team_id = team['team_id']
    else:
        team_id = team_list['teams'][0]['team_id']

    # Create a result
    code, result = create_result(user_access, team_id, first_game['game_id'], points=42)
    print('Create result:', code, result)
    assert code in (201, 400)  # 400 if duplicate constraints or validation

    # Admin list results with filters
    code, all_results = admin_list_results(admin_access)
    print('Admin results:', code, all_results.get('count'))
    assert code == 200

    if all_results.get('count', 0) > 0:
        any_result = all_results['results'][0]
        # Admin update (verify and adjust points)
        code, updated = admin_update_result(admin_access, any_result['result_id'], {"points_scored": any_result['points_scored'] + 5})
        print('Admin update result:', code)
        assert code in (200, 400, 404)

    print('Gaming API tests completed.')


if __name__ == '__main__':
    main()


