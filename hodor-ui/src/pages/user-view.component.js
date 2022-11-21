import * as Yup from 'yup';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton, TextField, MenuItem, Typography } from '@mui/material';
import { useState } from 'react';

const UsersActions = ({ user, handleDelete, handleSave }) => {
    return (
        <>
            <IconButton aria-label="save" onClick={() => { handleSave(user) }}>
                <SaveIcon fontSize='small' color='primary' />
            </IconButton>

            <IconButton aria-label="delete" onClick={() => { handleDelete(user) }}>
                <DeleteIcon fontSize='small' color='error' />
            </IconButton>

        </>
    );
};

const UsersRole = ({ user, roles }) => {
    // console.log(user)
    const _original_role = user.role
    const [currentRole, setCurrentRole] = useState(user.role)
    // console.log(roles)
    return (
        <TextField
            id="select-role"
            fullWidth
            select
            variant='outlined'
            // color='secondary'
            label=""
            size='small'
            value={currentRole.name}
            onChange={(e) => {
                const _role = e.target.value
                const [existing_role] = roles.items.filter(role => role.name == _role)
                if (existing_role) {
                    user.role = existing_role
                    setCurrentRole(existing_role)
                }
            }}
            helperText=""
        >
            {roles && roles.items.map(role => (
                <MenuItem key={role.name} value={role.name} color='secondary'>
                    <Typography color='secondary'>{role.name}</Typography>
                </MenuItem>
            ))}

        </TextField>
    );
}

const UsersEmail = ({ user, edit, setEdit, setError }) => {
    const _original_email = user.email;
    const row_id = user.id
    const handleEmailChanged = (e) => {

        if (e.key === 'Enter') {
            const _email = e.target.value
            console.log('entered');
            console.log(_email)
            const is_valid = Yup.string().email('Invalid email format').required('Email is required').isValidSync(_email)
            if (!is_valid) {
                setError(Error('Invalid email'))
            } else {
                user.email = _email
                setEdit({})
                setError(null)
            }
        }
    }

    if (edit && edit[row_id]) {
        console.log('Editable email')
        console.log(row_id)
        console.log(edit[row_id])
        console.log(edit)
        return (
            <input autoFocus type="text" id={`${row_id}-email`} placeholder={_original_email}
                onBlur={e => {
                    console.log('focus out')
                    setEdit({})
                }}
                onKeyDown={handleEmailChanged}></input>
        )
    }
    return (
        <span onClick={(e) => {
            console.log(`Editing email ${_original_email}`)
            console.log(e.target.value)
            const newEdit = {
                ...edit,
                [row_id]: { email: _original_email }
            };
            setEdit(newEdit)
            console.log(newEdit)

        }
        } className="text-primary" >
            {_original_email}
        </span >
    );
}

const UserView = ({ user, roles, edit, setEdit, setError, handleDelete, handleSave }) => {
    return (
        <div className='card mt-0 mb-2 pb-2 ps-2 pe-2 ms-2 me-2'>
            <div className='card-header mb-0 text-center bg-info'>
                {user.username}
            </div>

            <div class="card-body ps-0 pb-1 pt-2 pe-3  bg-light">
                <div className='row no-gutter ps-0'>
                    <div className='col-sm-12 ms-0 me-0 pe-0 d-flex justify-content-between'>
                        <UsersEmail user={user} edit={edit} setEdit={setEdit} setError={setError} />
                        <UsersRole user={user} roles={roles} />
                    </div>
                </div>
                <p class="card-text">
                    <UsersActions user={user} handleDelete={handleDelete} handleSave={handleSave} />
                </p>

            </div>
        </div>
    )

};
export { UserView, UsersActions, UsersEmail, UsersRole };