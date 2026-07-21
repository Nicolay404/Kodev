import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebRTCProps {
  roomToken: string | null;
}

export function useWebRTC({ roomToken }: UseWebRTCProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const remoteStreamRef = useRef<MediaStream | null>(null);

  const connectWebSocket = useCallback((token: string) => {
    // Determine WS protocol based on HTTP protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_BFF_URL ? new URL(import.meta.env.VITE_BFF_URL).host : window.location.host;
    
    // Connect to BFF signaling endpoint
    const wsUrl = `${protocol}//${host}/ws/teleconsult/${token}/`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setError('Error en la conexión de señalización');
    
    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      const pc = pcRef.current;
      if (!pc) return;

      try {
        if (message.type === 'offer') {
          await pc.setRemoteDescription(new RTCSessionDescription(message.offer));
          const answer = await pc.createAnswer();
          await pc.setLocalDescription(answer);
          ws.send(JSON.stringify({ type: 'answer', answer }));
        } else if (message.type === 'answer') {
          await pc.setRemoteDescription(new RTCSessionDescription(message.answer));
        } else if (message.type === 'ice-candidate') {
          await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
        }
      } catch (err) {
        console.error('Error handling signaling message', err);
        setError('Error procesando la señalización');
      }
    };
  }, []);

  const initPeerConnection = useCallback(() => {
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        // STUN/TURN as specified by architecture
        { urls: "turn:turn.samr.local:3478", username: "samr_user", credential: "samr_password" },
      ],
    });

    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate
        }));
      }
    };

    pc.ontrack = (event) => {
      // Remote stream received
      if (!remoteStreamRef.current) {
        remoteStreamRef.current = new MediaStream();
      }
      remoteStreamRef.current.addTrack(event.track);
    };

    pcRef.current = pc;
    return pc;
  }, []);

  useEffect(() => {
    if (roomToken) {
      initPeerConnection();
      connectWebSocket(roomToken);
    }

    return () => {
      // Cleanup
      pcRef.current?.close();
      wsRef.current?.close();
      localStreamRef.current?.getTracks().forEach(track => track.stop());
    };
  }, [roomToken, initPeerConnection, connectWebSocket]);

  return {
    isConnected,
    error,
    localStream: localStreamRef.current,
    remoteStream: remoteStreamRef.current,
  };
}
