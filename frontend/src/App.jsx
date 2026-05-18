import { useEffect, useState } from 'react'

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />

                <Route path="/admin" element={<h1>Admin page</h1>} />
                <Route path="/manager" element={<h1>Manager page</h1>} />
                <Route path="/team-member" element={<h1>Team member page</h1>} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
