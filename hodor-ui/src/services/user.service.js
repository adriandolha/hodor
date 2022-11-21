import authHeader from './auth-header';
import { API_URL } from '../pages/config';

class UserService {

    get_all() {
        return fetch(`${API_URL}/users`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    get_roles() {
        return fetch(`${API_URL}/roles`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    get_permissions() {
        return fetch(`${API_URL}/permissions`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    add_permission(permission) {
        return fetch(`${API_URL}/permissions`, {
            method: 'post',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify({ 'id': permission, 'name': permission })
        })
    }

    add_role(role) {
        return fetch(`${API_URL}/roles`, {
            method: 'post',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(role)
        })
    }

    add_user(user) {
        return fetch(`${API_URL}/users`, {
            method: 'post',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(user)
        })
    }
    delete_permission(permission) {
        return fetch(`${API_URL}/permissions/${permission}`, {
            method: 'delete',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            })
        })
    }
    delete_role(role) {
        return fetch(`${API_URL}/roles/${role.name}`, {
            method: 'delete',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            })
        })
    }
    delete_user(username) {
        return fetch(`${API_URL}/users/${username}`, {
            method: 'delete',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            })
        })
    }
    update_user(user) {
        return fetch(`${API_URL}/users/${user.username}`, {
            method: 'put',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(user)
        })
    }
    update_role(role) {
        return fetch(`${API_URL}/roles/${role.name}`, {
            method: 'put',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(role)
        })
    }
}

export default new UserService();