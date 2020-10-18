An animated background, using art from "Brony Polka Animated"

If you want to compile it, you can use the tool nix (only work on mac, linux and freebsd -- althought tested only on linux).

An exmple command line:
nix-build --arg x 1000 --arg y 1000 --arg frame_rate 60
output will be the result file. You should move and rename it with a .webp extension.
