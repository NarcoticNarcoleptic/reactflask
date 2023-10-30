import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

export default function TerminalComponent() {
  const terminalRef = useRef(null);
  const fitAddon = useRef(new FitAddon());
  const terminal = useRef(null);

  useEffect(() => {
    const term = new Terminal();
    term.loadAddon(fitAddon.current);
    term.open(terminalRef.current);
    terminal.current = term;

    // Run tmux in the terminal
    const tmuxSession = require('child_process').spawn('tmux', ['new-session', '-A', '-s', 'mytmuxsession']);

    // Listen to the output of tmux
    tmuxSession.stdout.on('data', (data) => {
      terminal.current.write(data.toString('utf8'));
    });

    // Resize the terminal to fit its container
    fitAddon.current.fit();

    return () => {
      tmuxSession.kill();
      terminal.current.dispose();
    };
  }, []);

  return <div ref={terminalRef} style={{ height: '100%', width: '100%' }}></div>;
}
