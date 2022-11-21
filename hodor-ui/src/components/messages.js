import { Snackbar, Alert } from '@mui/material';

const Message = ({message, severity, onExit}) => {
    return (
        <Snackbar open={true} autoHideDuration={6000} onClose={onExit}>
            <Alert severity={severity} sx={{ width: '100%' }}>
                {message}
            </Alert>
        </Snackbar>
    );

}
function Error({ message, onExit }) {
    return (
        <Message message={message} onExit={onExit} severity="error"/>
    );
}

function Success({ message, onExit }) {
    return (
        <Message message={message} onExit={onExit} severity="success"/>
    );
}

export {Error, Success};
