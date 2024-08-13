import React, { useState } from "react";
import "./CreateCardlet.css";
import img1 from "./img1.jpg"; // Ensure you have an appropriate image

const CreateCardlet = () => {
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    email: "",
    wishes: "",
    deliveryDate: "",
    imageFile: null,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, imageFile: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const apiUrl = `http://${process.env.REACT_APP_BACKEND_IP}:7000/create_cardlet`;

    const formDataToSend = new FormData();
    formDataToSend.append("from", formData.from);
    formDataToSend.append("to", formData.to);
    formDataToSend.append("email", formData.email);
    formDataToSend.append("wishes", formData.wishes);
    formDataToSend.append("deliveryDate", formData.deliveryDate);
    formDataToSend.append("image", formData.imageFile);

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formDataToSend, // sending formData as FormData object
      });

      const data = await response.json();

      if (response.ok) {
        alert("Cardlet created successfully! Wait for it to be delivered.");
        setFormData({
          from: "",
          to: "",
          email: "",
          wishes: "",
          deliveryDate: "",
          imageFile: null,
        });
      } else {
        console.error("Failed to create cardlet:", data.message);
        alert("Failed to create cardlet. Please try again.");
      }
    } catch (error) {
      console.error("An error occurred:", error);
      alert("An error occurred, please try again.");
    }
  };

  return (
    <div className="cardlet-container">
      <div className="cardlet-card">
        <div className="cardlet-left">
          <h2>Create a Cardlet!</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input
                type="text"
                id="from"
                name="from"
                placeholder="From"
                value={formData.from}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="text"
                id="to"
                name="to"
                placeholder="To"
                value={formData.to}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="email"
                id="email"
                name="email"
                placeholder="Recipient's Email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="datetime-local"
                id="deliveryDate"
                name="deliveryDate"
                value={formData.deliveryDate}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <textarea
                id="wishes"
                name="wishes"
                placeholder="Your Wishes"
                value={formData.wishes}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="file"
                id="imageFile"
                name="imageFile"
                accept="image/*"
                onChange={handleFileChange}
                required
              />
            </div>
            <div className="form-footer">
              <button type="submit" className="submit-button">
                Send Wishes
              </button>
            </div>
          </form>
        </div>
        <div className="cardlet-right">
          <div className="cardlet-image">
            <img src={img1} alt="Illustration" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateCardlet;
