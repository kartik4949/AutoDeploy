
from collections import namedtuple
from icevision.all import tfms, Dataset, ClassMap, models, torch
from torch_snippets import BB, choose, P, read, logger, lzip, detach, np, inspect, resize
from register import PREPROCESS, POSTPROCESS

infer_tfms = tfms.A.Adapter([
        # *tfms.A.resize_and_pad(size=224),
        tfms.A.Normalize()
    ])


Pred = namedtuple('Pred', ['bbs','labels'])

def preds2bboxes(preds):
    bboxes = [pred.pred.detection.bboxes for pred in preds]
    bboxes = [[(bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax) for bbox in bboxlist] for bboxlist in bboxes]
    bboxes = [[BB(int(x), int(y), int(X), int(Y)) for (x,y,X,Y) in bboxlist] for bboxlist in bboxes]
    return bboxes

def infer(fpaths=None, folder=None):
    if not fpaths:
        fpaths = []
        image_extns = ['png','jpg','jpeg']
        for extn in image_extns:
            fpaths += P(folder).Glob(f'*.{extn}')
        fpaths = choose(fpaths, 4)
    imgs = [read(f, 1) for f in fpaths]
    logger.info(f'Found {len(imgs)} images')

    infer_ds = Dataset.from_images(imgs, config.testing.preprocess, class_map=parser.class_map)
    infer_dl = model_type.infer_dl(infer_ds, batch_size=1)
    preds = model_type.predict_from_dl(model, infer_dl, keep_images=True)
    show_preds(preds=preds, ncols=3)
    return preds

def post_process(preds, images):
    size = 224
    bboxes = preds2bboxes(preds)
    shapes = [im.shape for im in images]
    pads = [((max(W, H) - min(W, H)) // 2) for H,W,_ in shapes]
    ws = [max(sh) for sh in shapes]
    bboxes = [[bb.remap((size,size), (ws[ix], ws[ix])) for bb in bblist] for ix, bblist in enumerate(bboxes)]
    # bboxes = [[BB(x,y-pads[ix],X,Y-pads[ix]) for (x,y,X,Y) in bbs] for ix,(sh, bbs) in enumerate(zip(shapes, bboxes))]
    _bboxes = []
    for ix, (sh, bbs) in enumerate(zip(shapes, bboxes)):
        w, h, _ = sh
        if w < h:
            _bboxes.append([BB(x,y-pads[ix],X,Y-pads[ix]) for (x,y,X,Y) in bbs])
        else:
            _bboxes.append([BB(x-pads[ix],y,X-pads[ix],Y) for (x,y,X,Y) in bbs])
    bboxes = _bboxes

    labels = [pred.pred.detection.labels for pred in preds]
    preds = lzip(bboxes, labels)
    preds = [Pred(*pred) for pred in preds]
    return preds

image_extns = ['jpg','jpeg','png']

@PREPROCESS.register_module('my_preprocess', force=True)
def preprocess(image):
    class_map = ClassMap(['truck','bus'])
    # images = [read(image_path, 1) for image_path in fpaths]
    image = np.asarray(image[0])
    shape = image.shape[:2]
    image = resize(image.astype(np.uint8), (224, 224))
    images = [image]

    infer_ds = Dataset.from_images(
        images, infer_tfms, 
        class_map=class_map)
    model_type = models.ultralytics.yolov5
    infer_dl = model_type.infer_dl(infer_ds, batch_size=1, drop_last=False)
    tensor, records = next(iter(infer_dl))
    x = tensor[0][0]
    x = np.array(x.detach().cpu())
    cache = (records, x, images, shape)
    return x, cache

# output = model.eval()(x)

@POSTPROCESS.register_module('my_postprocess', force=True)
def postprocess(output, cache, detection_threshold=0.25, nms_iou_threshold=0.45):
    preds = []
    records, x, images, shape = cache
    model_type = models.ultralytics.yolov5
    convert_raw_predictions = model_type.prediction.convert_raw_predictions
    if isinstance(output, np.ndarray):
        output = torch.Tensor(output)
    output = detach(output)
    pred = convert_raw_predictions(
        x[None], output, records,
        detection_threshold=detection_threshold,
        nms_iou_threshold=nms_iou_threshold
    )
    preds.extend(pred)
    bbs, clss = post_process(preds, images)[0]
    bbs = [bb.remap((224,224), shape) for bb in bbs]
    preds = [(x,y,X,Y,cls) for (x,y,X,Y), cls in zip(bbs, clss)]
    return {'out': preds, 'status': 200}
