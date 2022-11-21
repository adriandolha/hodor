import React, { useEffect, useState } from 'react'
import { withFormik, Form, Field } from 'formik'
import CircularProgress from '@mui/material/CircularProgress';

import { useNavigate } from 'react-router';
import { useSearchParams } from 'react-router-dom';
import * as Yup from 'yup';
import GoogleIcon from '@mui/icons-material/Google';
import { Box, TextField, Button, Typography, FormGroup, Paper } from '@mui/material';
import { API_URL } from '../pages/config';
import { Error, Success } from '../components/messages'

const LoginPage = (props) => {
    const GOOGLE_LOGIN_URL = `${API_URL}/google/login`
    const navigate = useNavigate()

    const {
        values,
        touched,
        errors,
        setFieldValue,
        handleSubmit,
        isSubmitting,
        setStatus,
        status,
        handleChange
    } = props;

    const [data, setData] = useState()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(false)
    const [searchParams] = useSearchParams();
    console.log(searchParams.get('state'));
    const state = searchParams && searchParams.get('state');

    useEffect(() => {
        let queryString = searchParams.toString();
        if (state) {
            console.log(queryString);
            fetch(`${API_URL}/google/token?${queryString}`, {
                method: 'get',
                headers: new Headers({
                    'Content-Type': 'application/json'
                })
            })
                .then(data => data.json())
                .then(setData)
                .then(() => setLoading(false))
                .catch((error) => {
                    console.log(error);
                    setError(error);
                });
        }
    }, [state]);


    if (isSubmitting) {
        console.log('Fetch login...')
        let loginType = values.login_type
        console.log(loginType)
        if (loginType === 'google') {
            window.location.href = GOOGLE_LOGIN_URL
        } else {
            login();

        }

    }

    if (data) {
        console.log(data)
        if (data.access_token) {
            localStorage.setItem("user", JSON.stringify(data));
            navigate('/profile')
            window.location.reload();
        }
    }
    if (loading && isSubmitting) {
        return <Box sx={{ display: 'flex' }}>
            <CircularProgress />
        </Box>
    }
    console.log(`Error is ${error}`)
    return (
        <Box sx={{justifyContent: 'center'}}>
            <Typography variant="h2" component="h2">Login</Typography>
            <Form >
                <FormGroup sx={{ marginBottom: 1, marginTop: 1 }}>
                    <TextField
                        // fullWidth
                        id="username"
                        name="username"
                        label="Username"
                        value={values.username}
                        onChange={handleChange}
                        error={touched.username && Boolean(errors.username)}
                        helperText={touched.username && errors.username}
                        sx={{ marginBottom: 1 }}
                    />
                    <TextField
                        // fullWidth
                        id="password"
                        name="password"
                        label="Password"
                        type='password'
                        value={values.password}
                        onChange={handleChange}
                        error={touched.password && Boolean(errors.password)}
                        helperText={touched.password && errors.password}
                        sx={{ marginBottom: 1 }}

                    />
                </FormGroup>

                <Button type="submit" variant="contained" color="primary">
                    <Typography sx={{ marginLeft: 1 }}>
                        Login
                    </Typography>
                </Button>
                <Button type="submit" variant="contained" color="success" onClick={() => {
                    setFieldValue('login_type', 'google')
                    handleSubmit(values, props)
                }}
                    sx={{ margin: 1 }}>
                    <GoogleIcon />
                    <Typography sx={{ marginLeft: 1 }}>
                        Google
                    </Typography>
                </Button>

            </Form>
            {error && <Error message={error.message} />}
        </Box>
    )

    function login() {
        fetch(`${API_URL}/signin`, {
            method: 'post',
            headers: new Headers({
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(values)
        })
            .then(data => data.json())
            .then(setData)
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(error);
                setError(error);
            });
    }
    function googleLogin() {
        fetch(`${API_URL}/signin`, {
            method: 'post',
            headers: new Headers({
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(values)
        })
            .then(data => data.json())
            .then(setData)
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(error);
                setError(error);
            });
    }
}

const LoginFormik = withFormik({

    mapPropsToValues: (props) => {
        return {
            username: props.username || '',
            password: props.password || ''
        }
    },
    validationSchema: Yup.object().shape({
        username: Yup.string().required('Username is required'),
        password: Yup.string().required('Password is required')
    }),
    handleSubmit: (values, props) => {
        console.log(values);
        props.setSubmitting(false);
    }
})(LoginPage)



export default function Login() {
    return (
        <LoginFormik />
    )
}