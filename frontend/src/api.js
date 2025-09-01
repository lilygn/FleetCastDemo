import axios from 'axios';

const api = axios.create({
  baseURL:
  "https://fleetcastdemo.onrender.com" ||
    'http://localhost:8080',                                    
});

export default api;
