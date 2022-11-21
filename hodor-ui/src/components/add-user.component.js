import { withFormik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import UserService from '../services/user.service';
import { Grid, Stack, MenuItem, Button, Dialog, DialogTitle, FormGroup, TextField, Typography } from '@mui/material'
import { Error as ErrorMessage, Success } from './messages'

function AddUserPage(props) {
    const {
        values,
        touched,
        errors,
        handleChange,
        setFieldValue,
        handleSubmit,
        handleReset,
        isSubmitting,
        setSubmitting,
        setStatus,
        status,
        onSave
    } = props;
    const [error, setError] = useState(false)
    const [roles, setRoles] = useState()
    const fetch_roles = () => {
        UserService.get_roles()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); });
                }
                return res.json();
            })
            .then((res) => {
                setRoles(res)
            })
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });
    }

    useEffect(() => {
        fetch_roles();
    }, []);

    return (

        <Grid container spacing={3} sx={{ marginLeft: 3 }}>
            <Grid item xs={3}>
                <Form>
                    <Stack spacing={2} sx={{ marginBottom: 1, marginTop: 1 }}>
                        <TextField
                            // fullWidth
                            id="username"
                            name="username"
                            label="Username"
                            value={values.username}
                            onChange={handleChange}
                            error={touched.username && Boolean(errors.username)}
                            helperText={touched.username && errors.username}
                        />
                        <TextField
                            // fullWidth
                            id="email"
                            name="email"
                            label="Email"
                            value={values.email}
                            onChange={handleChange}
                            error={touched.email && Boolean(errors.email)}
                            helperText={touched.email && errors.email}
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
                        />
                        {roles && <TextField
                            id="select-role"
                            select
                            variant='outlined'
                            label=""
                            size='small'
                            value={values.role}
                            onChange={handleChange}
                            error={touched.role && Boolean(errors.role)}
                            helperText={touched.role && errors.role}
                        >
                            {roles && roles.items.map(role => (
                                <MenuItem key={role.name} value={role.name} color='secondary'>
                                    <Typography color='secondary'>{role.name}</Typography>
                                </MenuItem>
                            ))}

                        </TextField>}
                    </Stack>

                    <Button type="submit" variant="contained" color="primary">
                        <Typography sx={{ marginLeft: 1 }}>
                            Add
                        </Typography>
                    </Button>
                    <Button type="secondary" variant="contained" color="success" onClick={props.onClose}
                        sx={{ margin: 1 }}>
                        <Typography sx={{ marginLeft: 1 }}>
                            Close
                        </Typography>
                    </Button>

                </Form>
            </Grid>
            {errors && errors.submit && <ErrorMessage message={errors.submit.message} />}
            {error && <ErrorMessage message={error} />}

        </Grid >
    )
}

const AddUserFormik = withFormik({

    mapPropsToValues: (props) => {
        return {
            username: props.username || '',
            email: props.email || '',
            password: props.password || '',
            role: props.role || 'ROLE_USER'
        }
    },
    validationSchema: Yup.object().shape({
        username: Yup.string().required('Username is required').min(5).max(100),
        password: Yup.string().required('Password is required').min(10).max(100),
        email: Yup.string().email('Invalid email format').required('Email is required'),
        role: Yup.string().required('Role is required'),
    }),
    handleSubmit: (values, { setSubmitting, setErrors, setStatus, props }) => {
        console.log('Add user...')
        console.log(values.role)
        console.log(props.roles)

        const [existing_role] = props.roles.items.filter(role => role.name == values.role)
        const user = {
            username: values.username,
            email: values.email,
            password: values.password,
            role: existing_role
        }
        console.log(user)

        UserService.add_user(user)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => {
                        console.log(message);
                        throw new Error(message);
                    })
                }
                return res.json();
            })
            .then(data => {
                props.onSave()
            })
            .catch((_error) => {
                console.log(`Error: ${_error}`);
                setSubmitting(false);
                setErrors({ submit: _error });
            });
    }
})(AddUserPage)



export default function AddUser({ onSave, roles, handleClose, show }) {
    return (
        <Dialog
            fullScreen
            open={show}
            onClose={handleClose}
        >
            <DialogTitle sx={{ marginLeft: 3 }}>ADD NEW USER</DialogTitle>
            <AddUserFormik onSave={onSave} roles={roles} onClose={handleClose} />

        </Dialog>
    )
}