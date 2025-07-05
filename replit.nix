{ pkgs }: {
  deps = [
    pkgs.nodejs-18_x
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.yarn
    pkgs.supervisor
    pkgs.curl
    pkgs.bash
  ];
}