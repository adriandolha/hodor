const DRAWER_WIDTH = 240
const local = {
    API_URL: 'http://ecs-load-balancer-850455720.eu-central-1.elb.amazonaws.com/api'
    // API_URL: 'http://localhost:5000/api'
}

const env = () => {
    const host = window.location.host
    if (host.startsWith('localhost')) {
        return local;
    }
    
}

const API_URL = env().API_URL;

export { DRAWER_WIDTH, API_URL };
