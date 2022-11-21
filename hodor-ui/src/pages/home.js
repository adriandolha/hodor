import { Fragment } from 'react';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import { Typography, Avatar, Card, CardContent, CardActions, Button } from '@mui/material';
import { API_URL } from "../pages/config";
import authService from '../services/auth-service';
import Login from '../components/login';
const sign_in_url = `${API_URL}/billy/auth/sign_in/cognito`


export default function Home() {
    const currentUser = authService.getCurrentUser()
    console.log(window.location.origin)
    return (
        <Fragment>
            <Card sx={{width: '20%'}}>
                <CardContent>
                    
                    {currentUser ? <Typography variant="h6" sx={{
                        borderRadius: '10px',
                        marginTop: 1,
                        marginBottom: 1
                    }}>
                        Hodor is an authentication and authorization service.
                    </Typography> : <Login /> }
                </CardContent>
                <CardActions sx={{ marginBottom: 2 }}>
                    {currentUser ? (
                        <Button onClick={() => {
                            window.location.href = '/users'
                        }} sx={{
                            color: 'white',
                            backgroundColor: 'primary.main',
                            width: '100%'
                        }}>Let's go</Button>
                    ) : (
                        null
                    )}
                </CardActions>
            </Card>

        </Fragment>
    );
}
