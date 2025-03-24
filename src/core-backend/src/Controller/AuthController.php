<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class AuthController extends AbstractController
{
    #[Route('/login', name: 'login', methods:['GET'])]
    public function login(): Response
    {
        return $this->render('auth/index.html.twig', [
            'controller_name' => 'AuthController',
        ]);
    }

    #[Route('/login', name: 'login_post', methods:['POST'])]
    public function login_post(string $username, string $password): Response
    {
        // hash password
        // create login attempt
        // do lookup
        // conditionally respond with login attempt

        return $this->render('auth/index.html.twig', [
            'controller_name' => 'AuthController',
        ]);
    }

    #[Route('/logout', name: 'logout')]
    public function logout(): Response
    {
        return $this->render('auth/logout.html.twig', [
            'controller_name' => 'AuthController',
        ]);
    }
}
