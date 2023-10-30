import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

const Navbar = () => {
  return (
    <AppBar position="fixed" sx={{ top: 0 }}>
      <Toolbar sx={{ height: 10, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h7" component="div">
          My App
        </Typography>
        <div>
          <Button color="inherit">Home</Button>
          <Button color="inherit">About</Button>
          <Button color="inherit">Services</Button>
          <Button color="inherit">Contact</Button>
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
