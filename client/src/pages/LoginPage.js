import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

export default function SignInPage() {
    const [loggedIn, setLoggedIn] = useState(false);
    const [username, setUsername] = useState('');
    const [userId, setUserId] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        axios.post('/login', {username: username, userId: userId, password: password})
            .then(res => {
            if (res.data.success) {
              setLoggedIn(true);
            } else {
              alert(res.data.message);
            }
            })
            .catch(err => {
            console.log(err);
            });
    };

    return (
        <div className="text-center m-5-auto">
            <h2>Sign in to us</h2>
            <form action="/home" >
                <p>
                    <label>UserId</label><br/>
                    <input type="text" name="user_id" value={userId} onChange={e => setUserId(e.target.value)} required />

                </p>
                <p>
                    <label>Username</label><br/>
                    <input type="text" name="username" value={username} onChange={e => setUsername(e.target.value)} required />

                </p>
                <p>
                    <label>Password</label>
                    <Link to="/forget-password"><label className="right-label">Forget password?</label></Link>
                    <br/>
                    <input type="password" name="password" value={password} onChange={e => setPassword(e.target.value)} required />
                </p>
                <p>
                    <button id="sub_btn" onClick={handleLogin}>Login</button>
                   
                </p>
            </form>
            <footer>
                <p>First time? <Link to="/register">Create an account</Link>.</p>
                <p><Link to="/">Back to Homepage</Link>.</p>
            </footer>
        </div>
    )
}
