# VPN/Routing Conflict for Minikube

- When routing using VPNs such as Tailscale or corporate, it is possible for the traffic/communication to be routed to the VPN instead of the minikube IP and cause the minikube cluster to become unreachable mid-session. This is because corporate VPNs often install a broad `192.168.0.0/16 dev tun0` route sends the traffic to the VPN instead of the local minikube IP.
- To quickly check if the routing is correct, you can utilize the command `ip route get "$(minikube ip)"`:
    - If output is `192.168.49.2 dev br-...` then routing is correct, where `br-...` indicates a Linux bridge interface in Docker/minikube.
    - If output is `192.168.X.X/16 dev <vpn-interface>` or `192.168.49.2 via ...` then routing is incorrect.

The way to fix this if it occurs it to do the following to explicity route traffic through an alternative subnet like `10.49.0.0/24` if main subnet `192.168.49.0/24` is being blocked or taken up by the VPN:
```bash
minikube delete
minikube start --driver=docker --memory=4096 --cpus=2 --subnet=10.49.0.0/24
minikube ip
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
```
- The above commands will delete the existing minikube cluster and create a new one with a different subnet.
- So there are two scenarios to consider:
```bash
Default / Current:
192.168.49.1 = Ubuntu bridge interface
192.168.49.2 = Minikube node IP / API server

Alternative if VPN conflict:
10.49.0.1 = Ubuntu bridge interface
10.49.0.2 = Minikube node IP / API server
```