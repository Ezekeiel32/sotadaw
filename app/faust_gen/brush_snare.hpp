/* ------------------------------------------------------------
name: "brush_snare"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn BrushSnare -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __BrushSnare_H__
#define  __BrushSnare_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS BrushSnare
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float BrushSnare_faustpower2_f(float value) {
	return value * value;
}

class BrushSnare : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst3;
	FAUSTFLOAT fHslider1;
	float fConst4;
	float fRec2[2];
	float fVec2[2];
	float fConst5;
	int IOTA0;
	float fVec3[4096];
	float fConst6;
	float fRec1[2];
	float fRec4[2];
	float fVec4[2];
	float fVec5[4096];
	float fRec3[2];
	FAUSTFLOAT fHslider2;
	float fConst7;
	float fConst8;
	float fConst9;
	float fConst10;
	float fConst12;
	float fConst14;
	float fConst15;
	float fConst18;
	float fConst20;
	float fConst22;
	int iRec7[2];
	float fRec6[3];
	float fConst23;
	float fRec5[3];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	
 public:
	BrushSnare() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn BrushSnare -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "brush_snare.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/pole:author", "Julius O. Smith III");
		m->declare("filters.lib/pole:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/pole:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "brush_snare");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.005f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 0.1f * fConst0;
		fConst4 = 1.0f / fConst0;
		fConst5 = 0.25f * fConst0;
		fConst6 = 0.5f * fConst0;
		fConst7 = 0.45f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.009f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 0.24f * fConst0;
		float fConst11 = std::tan(15707.963f / fConst0);
		fConst12 = 2.0f * (1.0f - 1.0f / BrushSnare_faustpower2_f(fConst11));
		float fConst13 = 1.0f / fConst11;
		fConst14 = (fConst13 + -1.4142135f) / fConst11 + 1.0f;
		fConst15 = 1.0f / ((fConst13 + 1.4142135f) / fConst11 + 1.0f);
		float fConst16 = std::tan(6283.1855f / fConst0);
		float fConst17 = BrushSnare_faustpower2_f(fConst16);
		fConst18 = 2.0f * (1.0f - 1.0f / fConst17);
		float fConst19 = 1.0f / fConst16;
		fConst20 = (fConst19 + -1.4142135f) / fConst16 + 1.0f;
		float fConst21 = (fConst19 + 1.4142135f) / fConst16 + 1.0f;
		fConst22 = 1.0f / fConst21;
		fConst23 = 1.0f / (fConst17 * fConst21);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.0f);
		fHslider1 = FAUSTFLOAT(2e+02f);
		fHslider2 = FAUSTFLOAT(0.3f);
		fHslider3 = FAUSTFLOAT(0.9f);
		fHslider4 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		IOTA0 = 0;
		for (int l5 = 0; l5 < 4096; l5 = l5 + 1) {
			fVec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec1[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec4[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 4096; l9 = l9 + 1) {
			fVec5[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec3[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			iRec7[l11] = 0;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec6[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec5[l13] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual BrushSnare* clone() {
		return new BrushSnare();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("brush_snare");
		ui_interface->addHorizontalSlider("body", &fHslider2, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("swish", &fHslider3, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst3 * fSlow1);
		float fSlow3 = float(fHslider1);
		float fSlow4 = std::max<float>(1.48f * fSlow3, 23.44895f);
		float fSlow5 = std::max<float>(2e+01f, std::fabs(fSlow4));
		float fSlow6 = fConst4 * fSlow5;
		float fSlow7 = fConst5 / fSlow5;
		float fSlow8 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow4));
		int iSlow9 = int(fSlow8);
		int iSlow10 = iSlow9 + 1;
		float fSlow11 = std::floor(fSlow8);
		float fSlow12 = fSlow8 - fSlow11;
		float fSlow13 = fSlow11 + (1.0f - fSlow8);
		float fSlow14 = std::max<float>(fSlow3, 23.44895f);
		float fSlow15 = std::max<float>(2e+01f, std::fabs(fSlow14));
		float fSlow16 = fConst4 * fSlow15;
		float fSlow17 = fConst5 / fSlow15;
		float fSlow18 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow14));
		int iSlow19 = int(fSlow18);
		int iSlow20 = iSlow19 + 1;
		float fSlow21 = std::floor(fSlow18);
		float fSlow22 = fSlow18 - fSlow21;
		float fSlow23 = fSlow21 + (1.0f - fSlow18);
		float fSlow24 = fConst7 * fSlow3 * float(fHslider2);
		float fSlow25 = 1.0f / std::max<float>(1.0f, fConst10 * fSlow1);
		float fSlow26 = fConst15 * float(fHslider3);
		float fSlow27 = 0.6f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			int iTemp1 = 1 - iVec1[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow6 + fRec2[1]);
			fRec2[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = BrushSnare_faustpower2_f(2.0f * fRec2[0] + -1.0f);
			fVec2[0] = fTemp3;
			float fTemp4 = float(iVec1[1]);
			float fTemp5 = fSlow7 * fTemp4 * (fTemp3 - fVec2[1]);
			fVec3[IOTA0 & 4095] = fTemp5;
			fRec1[0] = 0.999f * fRec1[1] + fTemp5 - (fSlow13 * fVec3[(IOTA0 - iSlow9) & 4095] + fSlow12 * fVec3[(IOTA0 - iSlow10) & 4095]);
			float fTemp6 = ((iTemp1) ? 0.0f : fSlow16 + fRec4[1]);
			fRec4[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = BrushSnare_faustpower2_f(2.0f * fRec4[0] + -1.0f);
			fVec4[0] = fTemp7;
			float fTemp8 = fSlow17 * fTemp4 * (fTemp7 - fVec4[1]);
			fVec5[IOTA0 & 4095] = fTemp8;
			fRec3[0] = 0.999f * fRec3[1] + fTemp8 - (fSlow23 * fVec5[(IOTA0 - iSlow19) & 4095] + fSlow22 * fVec5[(IOTA0 - iSlow20) & 4095]);
			iRec7[0] = 1103515245 * iRec7[1] + 12345;
			fRec6[0] = 4.656613e-10f * float(iRec7[0]) - fConst22 * (fConst20 * fRec6[2] + fConst18 * fRec6[1]);
			fRec5[0] = fConst23 * (fRec6[2] + (fRec6[0] - 2.0f * fRec6[1])) - fConst15 * (fConst14 * fRec5[2] + fConst12 * fRec5[1]);
			float fTemp9 = fSlow27 * (fSlow26 * (fRec5[2] + fRec5[0] + 2.0f * fRec5[1]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fSlow25 * (fConst8 - fTemp0) + 1.0f)) + fSlow24 * (4.0f * fRec3[0] + 2.96f * fRec1[0]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow2 * (fConst1 - fTemp0) + 1.0f)));
			output0[i0] = FAUSTFLOAT(fTemp9);
			output1[i0] = FAUSTFLOAT(fTemp9);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			fRec2[1] = fRec2[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			fVec4[1] = fVec4[0];
			fRec3[1] = fRec3[0];
			iRec7[1] = iRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
