import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ChannelPage from "./pages/ChannelPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/channel/:username" element={<ChannelPage />} />
      </Routes>
    </Router>
  );
}

export default App;
