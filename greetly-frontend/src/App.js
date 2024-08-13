import { Routes, Route } from "react-router-dom";
import "./App.css";
import CreateCardlet from "./Cardlet/CreateCardlet";
import LoginPage from "./Login/LoginPage";
import SignUp from "./SignUp/SignUp";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/create_cardlet" element={<CreateCardlet />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  );
}

export default App;
