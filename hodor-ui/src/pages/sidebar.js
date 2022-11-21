import * as React from 'react';
import { Drawer, Avatar, Box } from '@mui/material';
import Link from '@mui/material/Link';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Dashboard from '@mui/icons-material/Dashboard';
import Task from '@mui/icons-material/Task';
import Category from '@mui/icons-material/Category';
import AccountBalance from '@mui/icons-material/AccountBalance';
import Logo from '../components/logo';
const drawerWidth = 240;

export default function Sidebar(props) {
    const { mobileOpen, handleDrawerToggle } = props;
    const menuColor = 'primary'
    const drawer = <>
        <Toolbar sx={{ backgroundColor: 'white' }}>
            <Logo />
        </Toolbar>
        <Divider />
        <List>
            <ListItem key="users" disablePadding component={Link} href="/users">
                <ListItemButton>
                    <ListItemIcon>
                        <Dashboard color={menuColor} />
                    </ListItemIcon>
                    <ListItemText primary="Users" />
                </ListItemButton>
            </ListItem>
            <ListItem key="roles" disablePadding component={Link} href="/roles">
                <ListItemButton>
                    <ListItemIcon>
                        <Dashboard color={menuColor} />
                    </ListItemIcon>
                    <ListItemText primary="Roles" />
                </ListItemButton>
            </ListItem>

            <ListItem key="profile" disablePadding component={Link} href="/profile">
                <ListItemButton>
                    <ListItemIcon>
                        <Dashboard color={menuColor} />
                    </ListItemIcon>
                    <ListItemText primary="Profile" />
                </ListItemButton>
            </ListItem>

        </List>
    </>
    // const container = window !== undefined ? () => window().document.body : undefined;

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <Drawer
                // container={container}
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{
                    keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                    display: { xs: 'block', sm: 'none' },
                    '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
            >
                {drawer}
            </Drawer>
            <Drawer
                variant="permanent"
                sx={{
                    display: { xs: 'none', sm: 'block' },
                    width: drawerWidth,
                    '& .MuiDrawer-paper': {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                    },
                }}
                open
                anchor='left'
            >
                {drawer}
            </Drawer>
        </Box>
    );
}
