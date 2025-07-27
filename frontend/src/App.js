import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './Header.jsx';
import Dashboard from './Dashboard.jsx';
import StationViewer from './Station.jsx';

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/station-viewer" element={<StationViewer />} />
      </Routes>
    </Router>
  );
}

export default App;
