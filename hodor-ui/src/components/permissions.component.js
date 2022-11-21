import { Error as ErrorMessage, Success } from "../components/messages";
import { Grid, Chip, Box, Typography, Tooltip, IconButton, Button, TextField, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import React, { useState, useEffect, useMemo } from "react";

const Permission = ({ perm, onDelete }) => {
    return <Chip color='secondary' label={perm.name} size='small' onDelete={() => {
        // console.log(`Removing permission ${perm.name}`)
        onDelete(perm)
    }}></Chip>
}
const PermissionsList = ({ values, onDelete }) => {
    // console.log('Permissions list render..')
    // console.log(values)
    return <Grid container spacing={1}>
        {values && values.map((perm) => {
            return <Grid item key={perm.name}>
                <Permission
                    perm={perm}
                    onDelete={(perm) => {
                        onDelete(perm)
                    }} />
            </Grid>
        })}
    </Grid>
}

const PermissionsSelect = ({ allPermissions, handlePermissionSelect }) => {
    const [selectedPermission, setSelectedPermission] = useState(allPermissions[0])
    // console.log(selectedPermission)
    return allPermissions &&
        <TextField
            id="select-permission"
            select
            variant='outlined'
            label="Permissions"
            size='small'
            value={selectedPermission.name}
            onChange={(e) => {
                console.log(e.target.value)
                const perm = allPermissions.filter(p => p.name == e.target.value)[0]
                setSelectedPermission(perm)
                handlePermissionSelect(perm)
            }}
        >
            {allPermissions && allPermissions.map(perm => (
                <MenuItem key={perm.name} value={perm.name} color='secondary'>
                    <Typography color='secondary' variant='body2'>{perm.name}</Typography>
                </MenuItem>
            ))}

        </TextField>
}
const Permissions = ({ values, allPermissions, onDelete, onAdd }) => {
    const [permissions, setPermissions] = useState(values)
    const [selectedPermission, setSelectedPermission] = useState(allPermissions[0])
    const handlePermissionSelect = (perm) => {
        setSelectedPermission(perm)
    }
    return (
        <Grid container spacing={1} >
            <Grid item container xs={4} sx={{marginTop: 1}}>
                <Grid item xs={12}>
                    <PermissionsSelect allPermissions={allPermissions} handlePermissionSelect={handlePermissionSelect} />
                    <Button variant='contained'
                        color='primary'
                        size='small'
                        sx={{ marginTop: 1, marginBottom:1, fontSize: '10px', display:'block' }}
                        onClick={() => {
                            // console.log('Adding permission')
                            // console.log('New permissions...')
                            const new_permissions = [...permissions, selectedPermission]
                            // console.log(new_permissions)
                            setPermissions(new_permissions)
                            onAdd && onAdd(selectedPermission)
                        }}>
                        ADD
                    </Button>
                </Grid >
                
            </Grid>
            <Grid item xs={8}>
                <PermissionsList values={permissions} onDelete={(perm) => {
                    setPermissions(permissions.filter(p => p.name != perm.name))
                    onDelete(perm)
                }} />
            </Grid>

        </Grid>
    )
}
export { Permissions, PermissionsList, PermissionsSelect };