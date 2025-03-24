<?php

namespace App\Controller;

use App\Service\BlenderService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;

final class GenerateController extends AbstractController
{
    private $blenderService;

    public function __construct(BlenderService $blenderService)
    {
        $this->blenderService = $blenderService;
    }

    #[Route('/generate', name: 'generate_molds', methods:['POST'])]
    public function generateMolds(Request $request): Response
    {
        // Hardcoded for now, later populate with ORM
        $brailleFilePath = '/data/revised-braille-pages/1.txt';
        $result = $this->blenderService->brailleToPositiveAndNegativeMolds($brailleFilePath);
        return $this->json($result);

        // return $this->render('generate/index.html.twig', [
        //     'controller_name' => 'GenerateController',
        // ]);
    }
}
