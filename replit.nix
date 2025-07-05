{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs-18_x
    pkgs.yarn
    pkgs.curl
    pkgs.bash
  ];
}