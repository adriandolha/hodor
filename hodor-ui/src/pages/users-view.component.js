import React, { useState, useEffect, useMemo } from "react";
import UserService from '../services/user.service';
import AddUser from "../components/add-user.component";
import CircularProgress from '@mui/material/CircularProgress';
import DataTable from '../components/data-table';
import { Error as ErrorMessage, Success } from "../components/messages";
import { Typography, Tooltip, IconButton, Button } from '@mui/material';

// import UsersViewList from "./user-view-list.component";
import { UsersActions, UsersRole } from "./user-view.component";
import AddIcon from '@mui/icons-material/Add';
function UsersView() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState();
    const [edit, setEdit] = useState({});
    const [showAddUser, setShowAddUser] = useState(false);
    const [roles, setRoles] = useState();
    const [error, setError] = useState();
    const [message, setMessage] = useState();
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(20);

    const handleAdd = () => {
        console.log(`Adding new user...`);

    }
    console.log('rendering')
    const handleSave = (user) => {
        console.log(`Saving user...`);
        const _user = user
        console.log(_user);
        UserService.update_user(_user)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); })
                }
                return res.json();
            })
            .then(res => fetch_users())
            .then(() => setMessage('User updated.'))
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });
    }
    const handleDelete = (user) => {
        console.log(`Adding new user...`);
        const _user = user
        console.log(_user);
        UserService.delete_user(_user.username)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { throw new Error(message); })
                }
                return res;
            })
            .then(res => fetch_users())
            .then(() => setMessage('User deleted.'))
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });

    }
    const fetch_users = () => {
        UserService.get_all()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { setLoading(false); throw new Error(message); })
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
    const fetch_roles = () => {
        UserService.get_roles()
            .then(res => {
                if (!res.ok) {
                    return res.json().then(message => { setLoading(false); throw new Error(message); })
                }
                return res.json();
            })
            .then(setRoles)
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(`Error: ${error}`);
                setError(error);
            });
    }
    useEffect(() => {
        fetch_users()
        fetch_roles()
    }, []);

    const columns = [
        { field: 'id', headerName: 'ID', width: 70, hide: true },
        {
            field: 'username',
            headerName: 'Username',
            width: 150,
            sortable: false,
            renderCell: (params) => <Tooltip title={`${params.value}`} ><Typography sx={{ fontWeight: 'bold' }}>{params.value}</Typography></Tooltip>
        },
        {
            field: 'email',
            headerName: 'Email',
            sortable: false,
            width: 200,
            renderCell: (params) => <Tooltip title={`${params.value}`} ><Typography color='primary'>{params.value}</Typography></Tooltip>
        },
        {
            field: 'role',
            headerName: 'Role',
            // type: 'number',
            sortable: false,
            width: 250,
            renderCell: (params) => <UsersRole user={params.row} roles={roles} />
        },
        {
            field: "actions",
            headerName: "Actions",
            valueGetter: (params) => {
                return ''
            },
            renderCell: (params) => <UsersActions user={params.row} handleDelete={handleDelete} handleSave={handleSave} />
        }
    ];

    if (roles && data && !loading) {
        const rows = data.items
        const rowCount = data.total
        return (
            <div className='row mt-4'>
                {error && <ErrorMessage message={error.message} onExit={() => { setError(null) }} />}
                {message && <Success message={message} onExit={() => { setMessage(null) }} />}

                <AddUser className='row mt-4' show={showAddUser}
                    handleClose={() => { setShowAddUser(false) }}
                    onSave={() => { setShowAddUser(false); fetch_users(); }} roles={roles}></AddUser>

                <DataTable columns={columns}
                    rows={rows}
                    rowCount={rowCount}
                    page={page} pageSize={pageSize}
                    setPage={setPage} setPageSize={setPageSize} />
                <Button color='primary' variant='contained'
                    onClick={() => setShowAddUser(true)}
                    sx={{ marginTop: 1 }}>
                    Add User<AddIcon sx={{ marginLeft: 1 }} />
                </Button>
            </div>
        );
    } else {
        return <CircularProgress />
    }
}

export default UsersView;