import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';

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

  const connectWebSocket = useCallback((token: string, accessToken: string) => {
    // La señalización WebSocket vive en el API Gateway (nginx), no en el BFF
    // (que solo expone /health y /dashboard/). Ver nginx/samr.conf: /ws/teleconsult/.
    // El consumer exige el JWT como query param `token`, además del room_token en la ruta
    // (ver teleconsult-service/consumers/webrtc_consumer.py).
    const gatewayUrl = import.meta.env.VITE_GATEWAY_URL || 'https://localhost';
    const url = new URL(gatewayUrl);
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';

    const wsUrl = `${protocol}//${url.host}/ws/teleconsult/${token}/?token=${encodeURIComponent(accessToken)}`;

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
    // Solo STUN público — no hay servidor TURN desplegado en este MVP
    // (ver samr/.env: WEBRTC_ICE_SERVERS=stun:stun.l.google.com:19302).
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
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
      if (!remoteStreamRef.current) {
        remoteStreamRef.current = new MediaStream();
      }
      remoteStreamRef.current.addTrack(event.track);
    };

    pcRef.current = pc;
    return pc;
  }, []);

  useEffect(() => {
    const accessToken = useAuthStore.getState().accessToken;
    if (roomToken && accessToken) {
      initPeerConnection();
      connectWebSocket(roomToken, accessToken);
    }

    return () => {
      pcRef.current?.close();
      wsRef.current?.close();
      localStreamRef.current?.getTracks().forEach(track => track.stop());
    };
  }, [roomToken, initPeerConnection, connectWebSocket]);

  const attachLocalStream = useCallback((stream: MediaStream) => {
    localStreamRef.current = stream;
    const pc = pcRef.current;
    if (pc) {
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));
    }
  }, []);

  return {
    isConnected,
    error,
    localStream: localStreamRef.current,
    remoteStream: remoteStreamRef.current,
    attachLocalStream,
  };
}
