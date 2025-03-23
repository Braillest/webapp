<?php

// src/Controller/OfflineController.php
namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class OfflineController extends AbstractController
{
    #[Route('/offline', name: 'offline')]
    public function offline(): Response
    {
        return $this->render('offline.html.twig');
    }
}
