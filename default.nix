{ pkgs ? import <nixpkgs> {}}:

with builtins;

let
	stdenv = pkgs.stdenv;
	export_script = ./export.py;

	image_number = 8;

	exportImage = source_svg: layer_name: stdenv.mkDerivation rec {
		name = "frame-exported-${layer_name}.png";

		phases = [ "buildPhase" "installPhase" ];

		src = source_svg;

		nativeBuildInputs = [ pkgs.python pkgs.inkscape ];

		buildPhase = ''
			cp -r ${imageDep}/* .
			cp ${src} tmp.svg
			python ${export_script} ${layer_name} ./tmp.svg ./tmp.png
		'';

		installPhase = "cp ./tmp.png $out";
	};

	imageDep = stdenv.mkDerivation {
		name = "frame-export-dependancies";

		phases = ["installPhase"];

		installPhase = ''
			mkdir $out
			cp ${./frame} $out/frame -r
		'';
	};

	exportedImages = builtins.genList (x: [(exportImage ./common.svg (builtins.toString x)) x]) image_number;

	exportedImagesFolder = stdenv.mkDerivation {
		name = "exported-images";
		phases = "installPhase";

		installPhase = ''
			mkdir $out
			${
				builtins.concatStringsSep
				"\n"
				(
					map
					(x: "cp ${builtins.elemAt x 0} $out/${builtins.toString (builtins.elemAt x 1)}.png")
					exportedImages
				)
			}
		'';
	};

	makeAnimatedBackgroundFrames = frame_rate: x: y: stdenv.mkDerivation {
		name = "animated-backgroud-frames-${builtins.toString frame_rate}fps-${builtins.toString x}x${builtins.toString y}";
		phases = [ "buildPhase" "installPhase" ];

		nativeBuildInputs = with pkgs; [ python3 python3Packages.pillow ];

		buildPhase = ''
			mkdir tmp_png
			python ${./make_anim.py} ${builtins.toString frame_rate} ${exportedImagesFolder} ./tmp_png ${builtins.toString x} ${builtins.toString y}
		'';

		installPhase = ''
			mkdir -p $out
			cp tmp_png/* $out
		'';
	};

	makeAnimatedBackground = frame_rate: x: y: let
		frames = makeAnimatedBackgroundFrames frame_rate x y;
		extension = "webp";
	in stdenv.mkDerivation {
		name = "animated-background-${builtins.toString frame_rate}fps-${builtins.toString x}x${builtins.toString y}.${extension}";

		phases = [ "buildPhase" "installPhase" ];

		nativeBuildInputs = with pkgs; [ ffmpeg-full ];

		buildPhase = ''
			ffmpeg -framerate ${builtins.toString frame_rate} -pattern_type glob -i "${frames}/*.png" -lossless 1 -loop 0 tmp.${extension}
		'';

		installPhase = ''
			cp tmp.${extension} $out
		'';
	};
in
	makeAnimatedBackground 24 1366 768
