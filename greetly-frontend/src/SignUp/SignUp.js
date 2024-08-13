// SignUp.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SignUp.css";
import img1 from "./img1.jpg";

const SignUp = () => {
  // Updated to use a single state object for form data
  const [formData, setFormData] = useState({
    FullName: "",
    Email: "",
    Password: "",
    confirmPassword: "",
  });

  const navigate = useNavigate(); // Hook for navigating programmatically

  // Function to handle changes in form inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // No need to redefine apiUrl here if it's not dynamic or expected to change
    const apiUrl = `http://${process.env.REACT_APP_BACKEND_IP}:7000/register`;

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        mode: "cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        console.log("Registration successful!");
        // Reset formData state
        setFormData({
          FullName: "",
          Email: "",
          Password: "",
          confirmPassword: "",
        });

        alert("Registration successful!");
        navigate("/login"); // Navigate to login page after registration
      } else if (response.status === 409) {
        alert("Email already exists. Please choose a different email.");
      } else {
        alert("Registration failed. Please try again.");
      }
    } catch (error) {
      alert(`Error occurred during registration: ${error.message}`);
    }
  };

  return (
    <div className="signup-card-container">
      <div className="signup-card">
        <div className="signup-card-left">
          <h2>Create your Greetly account!</h2>
          <form onSubmit={handleSubmit}>
            <div className="signup-form-group">
              <input
                type="text"
                id="name"
                name="FullName"
                placeholder="Full Name"
                value={formData.FullName}
                onChange={handleChange}
                required
              />
            </div>
            <div className="signup-form-group">
              <input
                type="email"
                id="email"
                name="Email"
                placeholder="Email"
                value={formData.Email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="signup-form-group">
              <input
                type="password"
                id="password"
                name="Password"
                placeholder="Password"
                value={formData.Password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="signup-form-group">
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
            <div className="signup-form-footer">
              <button type="submit" className="signup-submit-button">
                Sign Up
              </button>
            </div>
          </form>
        </div>
        <div className="signup-card-right">
          <div className="signup-card-image">
            <img src={img1} alt="Illustration" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
