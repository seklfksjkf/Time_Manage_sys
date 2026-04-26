import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def _request_json(method, url, token=None, payload=None, timeout=10):
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')

    req = Request(url=url, method=method, headers=headers, data=data)

    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body) if body else None
    except HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ''
        try:
            parsed = json.loads(body) if body else None
        except Exception:
            parsed = body
        return e.code, parsed
    except URLError as e:
        raise RuntimeError(f'Failed to reach server: {e}')


def assert_ok(name, status, data, expected_status=(200,)):
    print(f'  Status: {status}')
    if data:
        print(f'  Response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}')
    if status not in expected_status:
        raise AssertionError(f'[{name}] expected {expected_status}, got {status}, response={data}')


def main():
    base_url = os.getenv('TMS_BASE_URL', 'http://127.0.0.1:5000/api').rstrip('/')
    username = os.getenv('TMS_USERNAME', 'admin')
    password = os.getenv('TMS_PASSWORD', 'admin123')

    print('== Time Management System API Smoke Test ==')
    print('Base URL:', base_url)

    # 1) Login
    print('\n[1/10] POST /auth/login - User login')
    status, data = _request_json('POST', f'{base_url}/auth/login', payload={
        'username': username,
        'password': password
    })
    assert_ok('auth.login', status, data, expected_status=(200,))

    token = (data or {}).get('access_token')
    if not token:
        raise AssertionError('[auth.login] missing access_token in response')

    # 2) Profile
    print('\n[2/10] GET /auth/profile - Get user profile')
    status, data = _request_json('GET', f'{base_url}/auth/profile', token=token)
    assert_ok('auth.profile', status, data)

    # 3) Users list
    print('\n[3/10] GET /auth/users - List all users')
    status, data = _request_json('GET', f'{base_url}/auth/users', token=token)
    assert_ok('auth.users', status, data)

    # 4) Projects list
    print('\n[4/10] GET /projects - List all projects')
    status, data = _request_json('GET', f'{base_url}/projects', token=token)
    assert_ok('projects.list', status, data)

    projects = (data or {}).get('projects') or []
    if not projects:
        raise AssertionError('[projects.list] no projects returned; create a project first')
    project_id = projects[0].get('id')
    if not project_id:
        raise AssertionError('[projects.list] project missing id')

    # 5) Project detail
    print(f'\n[5/10] GET /projects/{project_id} - Get project detail')
    status, data = _request_json('GET', f'{base_url}/projects/{project_id}', token=token)
    assert_ok('projects.detail', status, data)

    # 6) Project members
    print(f'\n[6/10] GET /projects/{project_id}/members - Get project members')
    status, data = _request_json('GET', f'{base_url}/projects/{project_id}/members', token=token)
    assert_ok('projects.members', status, data)

    # 7) Project tasks
    print(f'\n[7/10] GET /tasks?project_id={project_id} - List project tasks')
    status, data = _request_json('GET', f'{base_url}/tasks?project_id={project_id}', token=token)
    assert_ok('tasks.list_by_project', status, data)

    # 8) Notifications unread count
    print('\n[8/10] GET /notifications/unread-count - Get unread notifications count')
    status, data = _request_json('GET', f'{base_url}/notifications/unread-count', token=token)
    assert_ok('notifications.unread_count', status, data)

    # 9) Dashboard overview
    print('\n[9/10] GET /dashboard/overview - Get dashboard statistics')
    status, data = _request_json('GET', f'{base_url}/dashboard/overview', token=token)
    assert_ok('dashboard.overview', status, data)

    # 10) AI duration suggestion
    print(f'\n[10/10] GET /ai/task-duration?project_id={project_id} - AI task duration suggestion')
    status, data = _request_json('GET', f'{base_url}/ai/task-duration?project_id={project_id}&title=SmokeTest&priority=medium', token=token)
    assert_ok('ai.task_duration', status, data)

    print('\n✅ All 10 smoke tests passed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('\n❌ Smoke test failed:', e)
        sys.exit(1)
