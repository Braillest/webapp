<?php

namespace App\Controller;

use App\Service\AuthService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

final class BrowseController extends AbstractController
{
    public function __construct(AuthService $authService)
    {
        $this->authService = $authService;
    }

    #[Route('/browse', name: 'app_browse')]
    public function index(Request $request): Response
    {
        $session = $request->getSession();

        // Require account auth
        $this->authService->authorize($session);

        return $this->render('browse/index.html.twig', [
            'controller_name' => 'BrowseController',
        ]);
    }
}
