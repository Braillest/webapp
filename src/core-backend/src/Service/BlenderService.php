<?php

namespace App\Service;

use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class BlenderService
{
    public function brailleToPositiveAndNegativeMolds(string $brailleFilePath): bool
    {
        $command = [
            'blender',
            '--background',
            '--python',
            '/braillest/python/generate_minimal_molds.py',
            '--',
            $brailleFilePath
        ];

        $process = new Process($command);
        $process->setTimeout(3600);
        $process->run();

        // executes after the command finishes
        if (!$process->isSuccessful())
        {
            throw new ProcessFailedException($process);
        }

        echo $process->getOutput();

        return true;
    }
}
