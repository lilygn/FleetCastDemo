import axios from 'axios';

const api = axios.create({
  baseURL:
    import.meta?.env?.VITE_API_URL ||       // Vite
    process.env.REACT_APP_API_URL || 
     " https://fleetcast.onrender.com" ||

    'http://localhost:8080',                                    
});

export default api;
