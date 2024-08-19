// This file acts as a ProtectedRoute component that checks if the user is authenticated before rendering the component.
import {Navigate} from 'react-router-dom';
import {jwtDecode} from 'jwt-decode';
import {api} from '../api';
import { REFRESH_TOKEN, ACCESS_TOKEN } from '../constants';
import {useState, useEffect} from 'react';


// This component is used to check if the user is authenticated before rendering the component.
function ProtectedRoute({element}){
    const [isAuthenticated, setIsAuthenticated] = useState(null);

    useEffect(() => {
        auth().catch(() => setIsAuthenticated(false));
    }, []);

    // This function is used to refresh the token if the token is expired.
    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try {
            // Calling api component to make a POST request to the /api/token/refresh/ endpoint with the refresh token.
            // The api component has the base URL and the Axios instance to make the request.
            const response = await api.post('/api/token/refresh/', {refresh: refreshToken});
            if (response.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, response.data.access);
                setIsAuthenticated(true);
            } else {
                setIsAuthenticated(false);
            }
        } catch (error){
            setIsAuthenticated(false);
            console.log(error);
        }
    };

    // This function is used to check if the user is authenticated.
    const auth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthenticated(false);
            return;
        }
        // Decoding the token to get the expiration time and checking if the token is expired.
        const decodedToken = jwtDecode(token);
        if (decodedToken.exp * 1000 < Date.now()) {
            try {
                await refreshToken();
            } catch (error) {
                setIsAuthenticated(false);
                return;
            }
        } else {
            setIsAuthenticated(true);
        }
    };

    // Placeholder text to show while the user is being authenticated.
    if (isAuthenticated === null) {
        return <div>Loading...</div>;
    }

    return isAuthenticated ? element : <Navigate to="/login" />;

}

export default ProtectedRoute;