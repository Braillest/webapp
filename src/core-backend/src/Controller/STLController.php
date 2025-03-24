<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

final class STLController extends AbstractController
{
    #[Route('/preview', name: 'preview')]
    public function preview(): Response
    {
        return $this->render('preview.html');
    }

    #[Route('/stl/{file}', name: 'stl')]
    public function index(string $file): BinaryFileResponse
    {
        $filePath = "/data/$file";

        if (!file_exists($filePath))
        {
            throw $this->createNotFoundException('File not found');
        }

        $response = new BinaryFileResponse($filePath);
        $response->setContentDisposition(ResponseHeaderBag::DISPOSITION_ATTACHMENT, $file);

        return $response;
    }
}
