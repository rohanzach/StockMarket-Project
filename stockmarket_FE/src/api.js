// This file is used to create an axios instance and set the base URL for the API. 
// It also includes an interceptor to add the Authorization header to the request if the user is logged in.
import axios from 'axios';
import { ACCESS_TOKEN } from './constants';

const api = axios.create({
    // Here we use the VITE_API_URL environment variable to set the base URL for the API.
    baseURL: import.meta.env.VITE_API_URL
    });
    
// This interceptor is used to add the Authorization header to the request if the user is logged in.
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default api;