import React, { useState, useEffect, useMemo } from "react";
import UserService from '../services/user.service';
import AddRole from "../components/add-role.component";
import CircularProgress from '@mui/material/CircularProgress';
import DataTable from '../components/data-table';
import { Error as ErrorMessage, Success } from "../components/messages";
import { Grid, Chip, Box, Typography, Tooltip, IconButton, Button, TextField, MenuItem } from '@mui/material';
import { UsersActions, UsersRole } from "./user-view.component";
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import { Permissions } from '../components/permissions.component'
function RolesView() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState();
    const [error, setError] = useState();
    const [edit, setEdit] = useState({});
    const [showAddRole, setShowAddRole] = useState(false);
    const [message, setMessage] = useState();
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(20);


    const handleSave = (role) => {
        console.log(`Saving role...`);
        console.log(role)
        UserService.update_role(role)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); })
                }
                return res.json();
            })
            .then(res => {
                setMessage('Saved role.')
                fetch_roles()
            })
            // .then(() => setLoading(false))
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });


    }
    const handleDelete = (role) => {
        console.log('Delete role.')
        UserService.delete_role(role)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { setLoading(false); throw new Error(message); });
                }
                return res;
            })
            .then(() => setMessage('Role deleted.'))
            .then(() => fetch_roles())
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });
    }


    const fetch_roles = () => {
        UserService.get_roles()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { setLoading(false); throw new Error(message); });
                }
                return res.json();
            })
            .then(setData)
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });
    }
    const [perms, setPerms] = useState()
    const [loadingPerms, setLoadingPerms] = useState(true)

    console.log(perms)

    const fetch_permissions = () => {
        UserService.get_permissions()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); });
                }
                return res.json();
            })
            .then((res) => {
                setPerms(res);
                setLoadingPerms(false)
            })
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
                setLoadingPerms(false);
            });
    }

    useEffect(() => {
        fetch_roles()
        fetch_permissions();
        console.log('Fetch complete...')
    }, []);
    if (loading || loadingPerms) {
        return <CircularProgress />
    }


    const RolesActions = ({ role, handleDelete, handleSave }) => {
        // console.log(role)
        return (
            <>
                <IconButton aria-label="save" onClick={() => { handleSave(role) }}>
                    <SaveIcon fontSize='small' color='primary' />
                </IconButton>

                <IconButton aria-label="delete" onClick={() => { handleDelete(role) }}>
                    <DeleteIcon fontSize='small' color='error' />
                </IconButton>

            </>
        );
    };

    const handleDeletePerm = (role, perm) => {
        console.log(role)
        const new_permissions = role.permissions.filter(p => p.name != perm.name)
        role.permissions = new_permissions
        console.log(perm)
        console.log(new_permissions)
    }

    const handleAddPerm = (role, perm) => {
        console.log(role)
        const new_permissions = [...role.permissions, perm]
        const new_role = { ...role, permissions: new_permissions }
        console.log(perm)
        console.log('Role new permissions')
        console.log(new_permissions)
        console.log(data)
        let new_data = {
            ...data, items: data.items.map(item => {
                if (item.name == role.name) {
                    return new_role
                }
                return item
            })
        }
        console.log('New data...')

        console.log(new_data)
        setData(new_data)
    }


    if (data && perms && !loading) {
        const rows = data.items
        const rowCount = data.total
        const columns = [
            { field: 'id', headerName: 'ID', width: 70, hide: true },
            {
                field: 'name',
                headerName: 'Name',
                width: 200,
                sortable: false,
                renderCell: (params) => <Tooltip title={`${params.value}`} ><Typography color='primary' sx={{ fontWeight: 'bold' }}>{params.value}</Typography></Tooltip>
            },
            {
                field: 'permissions',
                headerName: 'Permissions',
                // type: 'number',
                sortable: false,
                width: 450,
                renderCell: (params) => {
                    // console.log('Rendering permissions...')
                    // console.log(params.value)
                    return <Permissions values={params.value}
                        allPermissions={perms.items}
                        onDelete={(perm) => handleDeletePerm(params.row, perm)}
                        onAdd={(perm) => handleAddPerm(params.row, perm)}
                    />
                }
            },
            {
                field: "actions",
                headerName: "Actions",
                valueGetter: (params) => {
                    return ''
                },
                renderCell: (params) => {
                    // console.log('Params row')
                    // console.log(params.row)
                    return <RolesActions role={params.row} handleDelete={handleDelete} handleSave={handleSave} />
                }
            }
        ];
        return (
            <Grid container spacing={1}>
                {error && <ErrorMessage message={error.message} onExit={() => { setError(null) }} />}
                {message && <Success message={message} onExit={() => { setMessage(null) }} />}
                <AddRole show={showAddRole}
                    handleClose={() => { setShowAddRole(false) }}
                    onSave={() => { setShowAddRole(false);fetch_roles() }}></AddRole>

                <DataTable columns={columns}
                    rows={rows}
                    rowCount={rowCount}
                    page={page} pageSize={pageSize}
                    setPage={setPage} setPageSize={setPageSize}
                />
                <Button color='primary' variant='contained'
                    onClick={() => setShowAddRole(true)}
                    sx={{ marginTop: 1 }}>
                    Add Role<AddIcon sx={{ marginLeft: 1 }} />
                </Button>
                {error && <ErrorMessage message={error} />}
            </Grid>
        );
    }
}

export default RolesView;