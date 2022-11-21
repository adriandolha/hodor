import { API_URL } from "../pages/config";
import authHeader from "./auth-header";

class AuthService {
  login(username, password) {
    return fetch(`${API_URL}/signin`, {
      method: 'post',
      headers: new Headers({
        ...authHeader(),
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify({
        username,
        password
      })
        .then(response => {
          if (response.data.access_token) {
            localStorage.setItem("user", JSON.stringify(response.data));
          }

          return response.data;
        })
    })
  }
  register(username, email, password) {
    return fetch(`${API_URL}/signup`, {
      method: 'post',
      headers: new Headers({
        ...authHeader(),
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify({
        username,
        email,
        password
      })
    })

  }
  logout() {
    localStorage.removeItem("user");
    window.location.reload(true);
    window.location.href = "/home"
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));;
  }
}

export default new AuthService();
