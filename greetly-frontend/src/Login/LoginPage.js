import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginPage.css";
import img1 from "./img1.jpg";

const LoginPage = () => {
  const [formData, setFormData] = useState({
    Email: "",
    Password: "",
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Assuming your Flask API is reachable at the URL stored in the REACT_APP_API_URL environment variable
    const apiUrl = `http://${process.env.REACT_APP_BACKEND_IP}:7000`;

    try {
      const response = await fetch(`${apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          Email: formData.Email,
          Password: formData.Password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        navigate("/create_cardlet"); // or wherever you need to redirect the user after login
        alert(
          "Login successful! Please check your email and confirm the subscription.!"
        );
      } else {
        console.error("Login failed:", data.message);
        alert(data.message); // Or handle errors more gracefully
      }
    } catch (error) {
      console.error("An error occurred:", error);
      alert("An error occurred, please try again.");
    }
  };

  return (
    <div className="login-card-container">
      <div className="login-card">
        <div className="login-card-left">
          <h2>Welcome to Greetly!</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input
                type="email"
                id="email"
                name="Email"
                placeholder="email"
                value={formData.Email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                id="password"
                name="Password"
                placeholder="password"
                value={formData.Password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-footer">
              <button type="submit" className="submit-button">
                Sign in
              </button>
            </div>
          </form>
          <div className="or-divider">
            <span>or</span>
          </div>
          <Link to="/SignUp" className="google-signin">
            Sign Up
          </Link>
          <div className="create-account">
            <a href="#create-account">New to Greetly? Create Account</a>
          </div>
        </div>
        <div className="login-card-right">
          <div className="login-card-image">
            <img src={img1} alt="Illustration" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
