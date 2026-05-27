<?php
declare(strict_types=1);

$root = dirname(__DIR__);
$yamlPath = $root . '/../_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/MODULES_REGISTRY.yaml';
$outPath = $root . '/modules.php';

if (!is_file($yamlPath)) {
    fwrite(STDERR, "MODULES_REGISTRY.yaml not found at {$yamlPath}\n");
    exit(1);
}

$py = <<<'PY'
import json, pathlib, re, sys
import yaml

src = pathlib.Path(sys.argv[1])
data = yaml.safe_load(src.read_text(encoding='utf-8'))

for mod in data.get('modules', []):
    route = str(mod.get('route', '/'))
    route = route.replace('/sfa/book/', '/crop-book/')
    route = route.replace('/sfa/market/', '/market/')
    route = route.replace('/sfa/calc/', '/calc/')
    route = route.replace('/sfa/community/', '/community/')
    route = route.replace('/sfa/search/', '/search/')
    route = route.replace('/sfa/about/', '/about/')
    route = route.replace('/sfa/', '/')
    mod['route_runtime'] = route

for page in data.get('pages', []):
    route = str(page.get('route', '/')).replace('/sfa/', '/')
    page['route_runtime'] = route

print(json.dumps(data, ensure_ascii=False, default=str))
PY;

$tmp = tempnam(sys_get_temp_dir(), 'mods_py_');
if ($tmp === false) {
    fwrite(STDERR, "failed to create temp file\n");
    exit(1);
}
$pyFile = $tmp . '.py';
rename($tmp, $pyFile);
file_put_contents($pyFile, $py);

$cmd = 'python3 ' . escapeshellarg($pyFile) . ' ' . escapeshellarg($yamlPath);
$json = shell_exec($cmd);
@unlink($pyFile);

if (!is_string($json) || trim($json) === '') {
    fwrite(STDERR, "failed to generate JSON from YAML\n");
    exit(1);
}

$data = json_decode($json, true);
if (!is_array($data)) {
    fwrite(STDERR, "invalid JSON generated from YAML\n");
    exit(1);
}

$php = "<?php\n// DO NOT EDIT — regenerate from MODULES_REGISTRY.yaml\nreturn " . var_export($data, true) . ";\n";
file_put_contents($outPath, $php);

fwrite(STDOUT, "regenerated {$outPath}\n");
