import { withFormik, Form, Field, FieldArray } from 'formik';
import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import UserService from '../services/user.service';
import { Grid, Stack, CircularProgress, MenuItem, Button, Dialog, DialogTitle, FormGroup, TextField, Typography, FormControlLabel, Checkbox } from '@mui/material'
import { Error as ErrorMessage, Success } from './messages'
import { Permissions } from './permissions.component';

function AddRolePage(props) {
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
    const [perms, setPerms] = useState()
    const [loading, setLoading] = useState(true)
    const [selectedPermission, setSelectedPermission] = useState()
    const fetch_permissions = () => {
        UserService.get_permissions()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); });
                }
                return res.json();
            })
            .then((res) => {
                setPerms(res)
                setSelectedPermission(res.items[0].name)
                setLoading(false)
            })
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
                setLoading(false)
            });
    }

    useEffect(() => {
        fetch_permissions();
    }, []);

    const handlePermissionSelect = (e) => {
        console.log(e.target.value)
    }
    const [permissions, setPermissions] = useState(perms)
    if (loading) {
        return <CircularProgress />
    }
    return (
        <Grid container spacing={2} sx={{ marginLeft: 3 }}>
            <Grid item xs={10}>

                <Form>
                    <Grid container spacing={2} sx={{ marginBottom: 1, marginTop: 1 }}>
                        <Grid item container direction='column' xs={12}>
                            <TextField
                                // fullWidth
                                id="name"
                                name="name"
                                label="Name"
                                value={values.name}
                                onChange={handleChange}
                                error={touched.name && Boolean(errors.name)}
                                helperText={touched.name && errors.name}
                            />
                            <FormControlLabel control={<Checkbox defaultChecked onChange={(e) => {
                                console.log(e.target.checked)
                                values.default = e.target.checked
                            }} />} label="Default" />
                        </Grid>
                        <Grid item container xs={8}>
                            <Permissions values={values.permissions}
                                allPermissions={perms.items}
                                onAdd={(perm) => {
                                    values.permissions.push(perm)
                                }}
                                onDelete={(perm) => {
                                    values.permissions = values.permissions.filter(p => p.name != perm.name)
                                }} />

                        </Grid>
                    </Grid>

                    <Button type="submit" variant="contained" color="primary" size='small'>
                        <Typography sx={{ marginLeft: 1 }}>
                            Add
                        </Typography>
                    </Button>
                    <Button type="secondary" variant="contained" color="secondary" size='small' onClick={props.onClose}
                        sx={{ margin: 1 }}>
                        <Typography sx={{ marginLeft: 1 }}>
                            Close
                        </Typography>
                    </Button>

                </Form>
                {errors && errors.submit && <ErrorMessage message={errors.submit.message} />}
            </Grid>

        </Grid>
    )
}

const AddRoleFormik = withFormik({

    mapPropsToValues: (props) => {
        return {
            name: props.name || '',
            default: props.default || false,
            permissions: props.permissions || [],
        }
    },
    validationSchema: Yup.object().shape({
        name: Yup.string().required('Role name is required').min(5).max(100),
        default: Yup.bool().required(),
        permissions: Yup.array().min(1).required(),

    }),
    handleSubmit: (values, { setSubmitting, setErrors, setStatus, props }) => {
        console.log('Add role...')
        console.log(values)
        const role = {
            name: values.name,
            default: values.default,
            permissions: values.permissions
        }
        const add_role = () => {
            UserService.add_role(role)
                .then(res => {
                    if (!res.ok) {
                        return res.json().then(message => { throw new Error(message); })
                    }
                    return res.json();
                })
                .then(data => {
                    props.onSave()
                })
                .catch((error) => {
                    console.log(`Error: ${error}`);
                    setSubmitting(false);
                    setErrors({ submit: error });
                });
        }
        add_role()
    }
})(AddRolePage)



export default function AddRole({ onSave, show, handleClose }) {
    return (
        <Dialog
            fullScreen
            open={show}
            onClose={handleClose}
        >
            <DialogTitle sx={{ marginLeft: 0 }}>ADD NEW ROLE</DialogTitle>
            <AddRoleFormik onSave={onSave} onClose={handleClose} />
        </Dialog>

    )
}